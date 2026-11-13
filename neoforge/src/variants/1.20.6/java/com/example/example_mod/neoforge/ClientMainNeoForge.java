package com.example.example_mod.neoforge;

import com.example.example_mod.ClientMain;
import com.example.example_mod.Main;
import com.example.example_mod.config.gui.GeneralOptionsScreen;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.client.gui.IConfigScreenFactory;

@Mod(value = Main.MOD_ID, dist = Dist.CLIENT)
public final class ClientMainNeoForge {

    public ClientMainNeoForge(ModContainer container) {
        ClientMain.init();

        if (ModList.get().isLoaded("cloth_config")) {
            container.registerExtensionPoint(IConfigScreenFactory.class,
                    (modContainer, parent) -> GeneralOptionsScreen.create(parent));
        }
    }

}
